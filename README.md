# information-retrieval: READ ME before you start

## If you don't have experience with vite.js or React.js

- Download the code in a zip file
- Go to your terminal, cd to the working directory
- `cd frontend` and then `npm install` to get all the node modules essential for running this React App
- Run `npm run dev` under the `frontend` directory to start the environment. You should see something like running on `localhost:5173` when you successfully run the codes
- Now don't close the existing terminal, START A NEW TERMINAL and cd to current working directory again
- `cd backend` and then `npm install` to get the backend node modules. You should see a folder naming `node_modules` in your `backend` folder as well
- Run `npm run dev` under the `backend` directory to start the backend server. Upon success, you will see `Server started on PORT 8080` in your terminal
- Now you are good to go. But before I lose you, I want to tell you some limits about this webpage I built
  - **It is very slow. You have to wait for a few seconds until it gets all the results (you can observe your logs in the `backend` terminal)**
  - Please **refresh your page** everytime you want to search for a new query
  - Please select **two or more results in both French and English**, otherwise the webpage might crash
  - We have the code for Query Expansion, but we haven't analyze it, no worries, we will bring that up first thing on next version
