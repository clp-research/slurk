export SLURK_SERVER_ID=$(docker run -p 80:5000 -e SECRET_KEY=your-key -d slurk/server)
