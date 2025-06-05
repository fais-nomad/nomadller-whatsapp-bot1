require('dotenv').config();
const express = require('express');
const axios = require('axios');

const app = express();
app.use(express.json());

const PORT = process.env.PORT || 3000;
const TOKEN = process.env.WHATSAPP_TOKEN;
const PHONE_ID = process.env.PHONE_NUMBER_ID;

const packages = {
  bali: {
    name: 'Bali Tour',
    pdf: 'https://drive.google.com/uc?export=download&id=1SvSSBlG6mtQHbTKIusmi1G3JoTy-YQlV',
  },
  everest: {
    name: 'Everest Base Camp Trek',
    pdf: 'https://drive.google.com/uc?export=download&id=1YlmmVzr7BmhbUy5cJtLSLrInwatSmINT',
  },
  annapurna: {
    name: 'Annapurna Base Camp Trek',
    pdf: 'https://drive.google.com/uc?export=download&id=1BSPmeWLSl02WZgnamHT6FhjnbgQzOwbV',
  },
};

app.post('/webhook', async (req, res) => {
  try {
    const entry = req.body.entry && req.body.entry[0];
    const changes = entry && entry.changes && entry.changes[0];
    const value = changes && changes.value;
    const messages = value && value.messages;

    if (!messages) {
      return res.sendStatus(200);
    }

    const message = messages[0];
    const from = message.from;
    const msgBody = message.text && message.text.body.toLowerCase();

    if (msgBody === 'hi' || msgBody === 'hello' || msgBody === 'start') {
      await sendButtons(from);
    } else if (packages[msgBody]) {
      await sendPDF(from, packages[msgBody].pdf, packages[msgBody].name);
    } else {
      await sendText(from, `Sorry, I didn't understand that. Type *hi* to see packages.`);
    }

    res.sendStatus(200);
  } catch (error) {
    console.error('Webhook error:', error);
    res.sendStatus(500);
  }
});

async function sendText(to, text) {
  await axios.post(
    `https://graph.facebook.com/v17.0/${PHONE_ID}/messages`,
    {
      messaging_product: 'whatsapp',
      to,
      text: { body: text },
    },
    {
      headers: { Authorization: `Bearer ${TOKEN}` },
    }
  );
}

async function sendButtons(to) {
  const data = {
    messaging_product: 'whatsapp',
    to,
    type: 'interactive',
    interactive: {
      type: 'button',
      body: {
        text: 'Welcome to Nomadller! Please select a tour package:',
      },
      action: {
        buttons: [
          { type: 'reply', reply: { id: 'bali', title: 'Bali Tour' } },
          { type: 'reply', reply: { id: 'everest', title: 'Everest Base Camp Trek' } },
          { type: 'reply', reply: { id: 'annapurna', title: 'Annapurna Base Camp Trek' } },
        ],
      },
    },
  };

  await axios.post(`https://graph.facebook.com/v17.0/${PHONE_ID}/messages`, data, {
    headers: { Authorization: `Bearer ${TOKEN}` },
  });
}

async function sendPDF(to, pdfUrl, title) {
  const data = {
    messaging_product: 'whatsapp',
    to,
    type: 'document',
    document: {
      link: pdfUrl,
      filename: `${title}.pdf`,
    },
  };

  await axios.post(`https://graph.facebook.com/v17.0/${PHONE_ID}/messages`, data, {
    headers: { Authorization: `Bearer ${TOKEN}` },
  });
}

app.listen(PORT, () => {
  console.log(`Nomadller WhatsApp bot listening on port ${PORT}`);
});
