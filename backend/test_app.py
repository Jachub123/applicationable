import unittest
import json
from app import app

class TestApp(unittest.TestCase):

    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True 

    def test_login_success(self):
        response = self.app.post('/login',
                                 data=json.dumps({'username': 'testuser', 'password': 'testpass', 'jobTitle': 'software_developer'}),
                                 content_type='application/json')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn('access_token', data)
        self.assertIn('job_title', data)

    def test_login_missing_fields(self):
        response = self.app.post('/login',
                                 data=json.dumps({'username': 'testuser'}),
                                 content_type='application/json')
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertIn('error', data)

    def test_interview_unauthorized(self):
        response = self.app.get('/interview')
        self.assertEqual(response.status_code, 401)

    def test_interview_authorized(self):
        # First, login to get a token
        login_response = self.app.post('/login',
                                       data=json.dumps({'username': 'testuser', 'password': 'testpass', 'jobTitle': 'software_developer'}),
                                       content_type='application/json')
        token = json.loads(login_response.data)['access_token']

        # Then, use the token to access the interview endpoint
        response = self.app.get('/interview',
                                headers={'Authorization': f'Bearer {token}'})
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn('message', data)

if __name__ == '__main__':
    unittest.main()