"""Message View tests."""

# run these tests like:
#
#    FLASK_ENV=production python -m unittest test_message_views.py


import os
from unittest import TestCase

from models import db, connect_db, Message, User

# BEFORE we import our app, let's set an environmental variable
# to use a different database for tests (we need to do this
# before we import our app, since that will have already
# connected to the database

os.environ['DATABASE_URL'] = "postgresql:///warbler-test"


# Now we can import app

from app import app, CURR_USER_KEY

# Create our tables (we do this here, so we only create the tables
# once for all tests --- in each test, we'll delete the data
# and create fresh new clean test data

db.create_all()

# Don't have WTForms use CSRF at all, since it's a pain to test

app.config['WTF_CSRF_ENABLED'] = False


class MessageViewTestCase(TestCase):
    """Test views for messages."""

    def setUp(self):
        """Create test client, add sample data."""

        User.query.delete()
        Message.query.delete()

        self.client = app.test_client()

        self.testuser = User.signup(username="testuser",
                                    email="test@test.com",
                                    password="testuser",
                                    image_url=None)

        db.session.commit()
        
        self.testuser_id = new_user.id

        message_data = {
            "user_id":self.testuser_id,
            "text":"test_message"
        
        }
        message = Message(**message_data)
        db.session.add(message)
        db.session.commit()


    def test_add_message(self):
        """Can use add a message?"""

        # Since we need to change the session to mimic logging in,
        # we need to use the changing-session trick:

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id

            # Now, that session setting is saved, so we can have
            # the rest of ours test

            resp = c.post("/messages/new", data={"text": "Hello"})

            # Make sure it redirects
            self.assertEqual(resp.status_code, 302)

            msg = Message.query.one()
            self.assertEqual(msg.text, "Hello")

    def test_add_message_logged_out(self):

            with self.client as c:
             with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser_id

            # If we don't add text to the message, the form should be invalid

            resp = c.post(
                "/messages/new", 
                data={"text": ""}, 
                follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn("Add my message!", html)
            self.assertEqual(Message.query.count(), 1)
 

    def test_messages_show(self):
        """ Test to a message being shown. """

        with self.client as c:
         
            resp = c.get(f"/messages/{self.message_id}")
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn("test_message", html)

    def test_messages_destroy(self):
        """ Test deleting a message """
     
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser_id
    
            resp = c.post(
                f"/messages/{self.message_id}/delete",
                follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertNotIn("test_message", html)

            self.assertEqual(Message.query.count(), 0)

    def test_messages_destroy_dif_user(self):
        """ Test that you are prohibited from deleting a message as another user """

        new_user2 = User.signup(username="testuser2",
                            email="test2@test.com",
                            password="testuser2",
                            image_url=None)
        db.session.commit()

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = new_user2.id
    
            resp = c.post(
                f"/messages/{self.message_id}/delete",
                follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertEqual(Message.query.count(), 1)

    def test_messages_destroy_logged_out(self):
        """ Test that you are prohibited from deleting a message if not logged in"""
    
        with self.client as c:

            resp = c.post(
                f"/messages/{self.message_id}/delete",
                follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn("Access unauthorized.", html)