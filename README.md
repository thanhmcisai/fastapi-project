# fastapi-project

1. Create new ubuntu service:

- cd /etc/systemd/system/
- nano fastapi.service
  '''
  [Unit]
  Description=demo fastapi application
  After=network.target

[Service]
User=thanh
Group=thanh
WorkingDirectory=/home/thanh/app/src/
Environment="PATH=/home/thanh/app/venv/bin"
EnvironmentFile=/home/thanh/.env
ExecStart=/home/thanh/app/venv/bin/gunicorn -w 4 -k uvicorn.workers.UvicornWorker app.main:app --bind 0.0.0.0:8000

[Install]
WantedBy=multi-user.target
'''

- systemctl start fastapi
- systemctl status fastapi
- sudo systemctl enable fastapi # Enable service

2. Install Nginx

- sudo apt install nginx -y
- systemctl start nginx
- cd /etc/nginx/sites-available
- sudo vi default
  '''
  server {
  listen 80 default_server;
  listen [::]:80 default_server;

      server_name _; # replace with specific domain name like sanjeev.com

      location / {
          proxy_pass http://localhost:8000;
          proxy_http_version 1.1;
          proxy_set_header X-Real-IP $remote_addr;
          proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
          proxy_set_header Upgrade $http_upgrade;
          proxy_set_header Connection 'upgrade';
          proxy_set_header Host $http_host;
          proxy_set_header X-NginX-Proxy true;
          proxy_redirect off;
      }

  }
  '''

- systemctl restart nginx

3. Setup SSL using CertBot

- Tutorial: https://certbot.eff.org/instructions?ws=nginx&os=ubuntufocal
- sudo snap install --classic certbot
- sudo certbot --nginx
- Check change in nginx: cat /etc/nginx/sites-available/default

4. Setup Firewall

- sudo ufw status # Check status of firewall
- sudo ufw allow <port/http/https/ssl/...> # Set port to open
- sudo ufw enable
- sudo ufw delete allow <port/http/https/ssl/...>

5. Testing

- pytest --disable-warnings -v -s -x
