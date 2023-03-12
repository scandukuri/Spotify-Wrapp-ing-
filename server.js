import express, { json } from 'express';
import fetch from 'node-fetch';
import { fileURLToPath } from 'url';
import path from 'path';
import { spawn } from 'child_process';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const app = express();
app.use(express.static('public'));

const redirect_uri = 'http://localhost:8888/callback';
const client_id = '915b0386b44c43348183c89a679f7e0a';
const client_secret = '71089ac558bd4bea8db1ceeadffe735a';

let access_token;

app.get('/', function (req, res) {
  res.sendFile(__dirname + '/index.html');
});

app.get('/authorize', function (req, res) {
  const scope = 'user-top-read';
  const url = `https://accounts.spotify.com/authorize?response_type=code&client_id=${client_id}&scope=${encodeURIComponent(scope)}&redirect_uri=${encodeURIComponent(redirect_uri)}`;
  res.redirect(url);
});

app.get('/callback', async (req, res) => {
  const code = req.query.code;

  const body = new URLSearchParams({
    code: code,
    redirect_uri: redirect_uri,
    grant_type: 'authorization_code',
  });

  const response = await fetch('https://accounts.spotify.com/api/token', {
    method: 'post',
    body: body,
    headers: {
      'Content-type': 'application/x-www-form-urlencoded',
      Authorization:
        'Basic ' + Buffer.from(client_id + ':' + client_secret).toString('base64'),
    },
  });

  const data = await response.json();
  access_token = data.access_token;

  // Call the Python script only after getting the access token
  const pythonProcess = spawn('python3', ['spotify_data.py']);

  // Send the access token to the Python script through stdin
  pythonProcess.stdin.write(access_token + '\n');
  pythonProcess.stdin.end();

  pythonProcess.stderr.on('data', (data) => {
    console.error('Error in Python script:', data.toString());
  });

  pythonProcess.stdout.on('data', (data) => {
    console.log('Received data from Python script:');
    try {
      const json_data = JSON.parse(data);
      app.set('json_data', json_data);
      console.log('Successfully parsed JSON data.');
      console.log(json_data);
    } catch (e) {
      console.error('Error parsing JSON:', e);
    }
  });

  res.redirect('/dashboard');
});

app.get('/dashboard', function (req, res) {
  res.sendFile(__dirname + '/dashboard.html');
});

app.get('/data', function(req, res) {
  const json_data = app.get('json_data');
  res.json(json_data)
});

const listener = app.listen(8888, function () {
  console.log(`Your app is listening on http://localhost:${listener.address().port}`);
});
