const fs = require('fs');
const path = require('path');

// Read file safely
function readFile(filePath) {
  try {
    return fs.readFileSync(path.join(__dirname, '..', filePath), 'utf8');
  } catch (e) {
    return '';
  }
}

// Parse todos from project files
function parseTodos(content) {
  const todos = [];
  const lines = content.split('\n');
  for (const line of lines) {
    if (line.includes('- [ ]')) {
      const dueMatch = line.match(/\[DUE: (\d{4}-\d{2}-\d{2})\]/);
      let task = line.replace('- [ ]', '').trim();
      if (dueMatch) {
        task = task.replace(dueMatch[0], '').trim();
      }
      task = task.replace(/\[BLOCKED\]/g, '').trim();
      if (task.length > 0) {
        todos.push({ task, due: dueMatch ? dueMatch[1] : null });
      }
    }
  }
  return todos;
}

// Parse hours from TIME.md
function parseHours(content) {
  const nedlMatch = content.match(/NËDL[\s\S]*?\*\*\w+ Total: ([\d.]+) hrs\*\*/);
  const nextitleMatch = content.match(/NexTitle[\s\S]*?\*\*\w+ Total: ([\d.]+) hrs\*\*/);
  return {
    nedl: nedlMatch ? nedlMatch[1] : '0',
    nextitle: nextitleMatch ? nextitleMatch[1] : '0'
  };
}

// Calculate days until due
function daysUntil(dateStr) {
  const today = new Date();
  today.setHours(0, 0, 0, 0);
  const due = new Date(dateStr + 'T00:00:00');
  const diff = Math.ceil((due - today) / (1000 * 60 * 60 * 24));
  return diff;
}

// Main
function generateEmail() {
  const today = new Date();
  const dayOfWeek = today.getDay(); // 0 = Sunday, 5 = Friday
  const isFriday = dayOfWeek === 5;
  
  const dateStr = today.toLocaleDateString('en-US', { 
    weekday: 'short', month: 'short', day: 'numeric', year: 'numeric' 
  });

  // Read all project files
  const projectsDir = path.join(__dirname, '..', 'projects');
  let allTodos = [];
  
  if (fs.existsSync(projectsDir)) {
    const files = fs.readdirSync(projectsDir).filter(f => f.endsWith('.md') && f !== 'INDEX.md');
    for (const file of files) {
      const content = fs.readFileSync(path.join(projectsDir, file), 'utf8');
      const todos = parseTodos(content);
      const clientMatch = content.match(/client: (\w+)/);
      const client = clientMatch ? clientMatch[1].toUpperCase() : 'UNKNOWN';
      todos.forEach(t => { t.client = client; allTodos.push(t); });
    }
  }

  // Read time
  const time = readFile('TIME.md');
  const hours = parseHours(time);

  // Categorize todos
  const overdue = allTodos.filter(t => t.due && daysUntil(t.due) < 0);
  const dueToday = allTodos.filter(t => t.due && daysUntil(t.due) === 0);
  const dueTomorrow = allTodos.filter(t => t.due && daysUntil(t.due) === 1);

  // DECISION: Should we send an email?
  const hasUrgent = overdue.length > 0 || dueToday.length > 0 || dueTomorrow.length > 0;
  const shouldSend = hasUrgent || isFriday;

  if (!shouldSend) {
    // Return null to signal "don't send"
    return { send: false };
  }

  // Build email
  let email = '';
  
  if (overdue.length > 0) {
    email += '🚨 OVERDUE:\n';
    overdue.forEach(t => {
      email += `• [${t.client}] ${t.task} (was due ${t.due})\n`;
    });
    email += '\n';
  }

  if (dueToday.length > 0) {
    email += '📅 DUE TODAY:\n';
    dueToday.forEach(t => {
      email += `• [${t.client}] ${t.task}\n`;
    });
    email += '\n';
  }

  if (dueTomorrow.length > 0) {
    email += '⏰ DUE TOMORROW:\n';
    dueTomorrow.forEach(t => {
      email += `• [${t.client}] ${t.task}\n`;
    });
    email += '\n';
  }

  // Friday hours review
  if (isFriday) {
    email += '📊 FRIDAY HOURS REVIEW:\n';
    email += `NËDL: ${hours.nedl} hrs this month\n`;
    email += `NexTitle: ${hours.nextitle} hrs this month\n`;
    email += 'Remember to log your hours before invoicing!\n\n';
  }

  email += '---\nOpen chief-of-stuff in Cursor for details.';

  // Subject line with urgency indicator
  let subject = `Chief of Staff - ${dateStr}`;
  if (overdue.length > 0) {
    subject = `🚨 OVERDUE - ${subject}`;
  } else if (dueToday.length > 0) {
    subject = `📅 Due Today - ${subject}`;
  } else if (isFriday) {
    subject = `📊 Friday Review - ${subject}`;
  }

  return {
    send: true,
    subject,
    body: email
  };
}

// Output as JSON for the workflow
const result = generateEmail();
console.log(JSON.stringify(result));
