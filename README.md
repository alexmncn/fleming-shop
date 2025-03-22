# Fleming Shop

Fleming Shop is an online catalog application designed for a physical store. It provides customers with an intuitive interface to browse products, check prices, and view stock availability, while giving administrators a secure platform to manage products and images.

## Overview

Fleming Shop is built with modern web technologies to ensure a smooth user experience and robust performance in production. The project consists of:

- **Frontend:**  
  Developed using Angular, the frontend delivers a responsive, user-friendly interface that serves as the entry point for customers.

- **Backend (API):**  
  Built with Flask, the backend processes user requests and implements business logic. It leverages Gunicorn as a WSGI server—acting as an intermediary between Flask and Apache—to securely expose the API in production.

- **Database Access:**  
  The backend connects to a database that stores all essential data, including user information, product details, and logs.
