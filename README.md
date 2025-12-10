# Auction Platform Web App

Web app that allows users to create, browse, bid on, and comment on auction listings in an eBay-like interface.

---
## Video Overview
[Watch the project overview](https://youtu.be/LcI1S3pxI0U)

---

## Features
- Create auction listings with title, description, starting bid, optional image, and category.
- Browse active listings and filter by category.
- View detailed listing pages with current bids, comments, and listing information.
- Place bids with validation to ensure they exceed the current highest bid.
- Add/remove listings from a personal watchlist.
- Close auctions as the listing owner, identifying the highest bidder as the winner.
- Post and view comments on listings.
- Manage listings, bids, and comments via Django Admin interface.

---

## Technologies
Python, Django, HTML, CSS, Bootstrap.

---

## Installation
1. Clone the repository:
   git clone https://github.com/saraccmululo/auction_platform_app.git
   cd auction_platform_app
2. Create a virtual environment:
    python3 -m venv env
    source env/bin/activate   # On Windows: env\Scripts\activate
3. Install dependencies:
    pip install -r requirements.txt
4. Run the Django server:
    python manage.py runserver
5. Open your browser at: http://127.0.0.1:8000/

Usage
Browse all active listings or filter by category.
Click on a listing to view details, bid, or comment.
Create a new listing from the “Create Listing” page.
Add listings to your watchlist and manage them.
Close auctions if you are the listing owner to finalize the winner.
