/**
 * Contact form receiver for jpenberth.com
 * Paste this into Extensions > Apps Script inside the Google Sheet that should collect messages.
 * Then: Deploy > New deployment > type "Web app" > Execute as: Me > Who has access: Anyone > Deploy.
 */
const NOTIFY_EMAIL = 'jpenberth@jpenberth.com';   // where each new message is emailed
const SHEET_NAME = 'Inquiries';
const MAX_LEN = 4000;

function doPost(e) {
  const p = (e && e.parameter) || {};
  // Spam trap: real visitors never see or fill this hidden field
  if (p.company) return ok_();

  const name = clean_(p.name, 120), email = clean_(p.email, 200), topic = clean_(p.topic, 60),
        message = clean_(p.message, MAX_LEN), page = clean_(p.page, 200);
  if (!name || !email || !message || email.indexOf('@') < 1) return ok_();

  const ss = SpreadsheetApp.getActiveSpreadsheet();
  let sh = ss.getSheetByName(SHEET_NAME);
  if (!sh) {
    sh = ss.insertSheet(SHEET_NAME);
    sh.appendRow(['Received', 'Name', 'Email', 'Topic', 'Message', 'Page']);
    sh.setFrozenRows(1);
  }
  sh.appendRow([new Date(), name, email, topic, message, page]);

  try {
    MailApp.sendEmail({
      to: NOTIFY_EMAIL,
      replyTo: email,
      subject: 'jpenberth.com: ' + (topic || 'New message') + ' from ' + name,
      body: 'Name: ' + name + '\nEmail: ' + email + '\nTopic: ' + topic + '\n\n' + message + '\n\n(Sent from ' + page + ')'
    });
  } catch (err) { /* the row is saved even if email fails */ }
  return ok_();
}

function clean_(v, max) { return String(v || '').replace(/[\u0000-\u0008\u000B\u000C\u000E-\u001F]/g, '').trim().slice(0, max); }
function ok_() { return ContentService.createTextOutput('ok'); }
