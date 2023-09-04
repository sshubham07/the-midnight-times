# the-midnight-times
Django News Application

Key Features:-
1. Once Signup or login is successful, then only user can search for news articles
2. Every searchkeyword will be added to history of the user and he /she can see his/her history reports
3. Any user can be blocked by admin in admin section using a table called block
4. Only Admin can view the graph of search keyword
5. If keyword is again serached within 15 minutes, the user won't get articles.
6.History is shown in sorted form, latest is shown first

To Run this project:-
1.pip install virtualenv
2.source venv/bin/activate(for Windows - venv\Scripts\activate)
3.pip install -r requirements.txt
4.python manage.py migrate
5.python manage.py runserver

# ScreenShots 
1.Home Page![home](https://github.com/sshubham07/the-midnight-times/assets/51732065/36f2c1c1-e014-43f1-a02d-1caf88514576) 
2.History Search of a user![history](https://github.com/sshubham07/the-midnight-times/assets/51732065/42aafdb8-7f81-47f0-98e4-0c7c796b1eae)

