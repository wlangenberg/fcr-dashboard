# FCR-Dashboard
Streamlit dashboard to display the electricity usage over time.

Visit the app at https://fcr-dashboard.streamlit.app

## To run in Docker
1. Start by building the docker image:  
`docker build -t streamlit-fcr .`

2. Run the image in a container and open port 80 to the app's port 8051:  
`docker run -p 80:8051 --name="streamlit-container" -d streamlit-fcr`
