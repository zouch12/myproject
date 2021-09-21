CS50 final Project - sportsdennery.com

The idea of this website is for the viewing of the public to know what sporting events are taking place in the community sportswise. It is mainly a soccer based website at his moment where non-players, players and coaches of the sport can all accept the webpage and recieve infomation. Person wishing to join particular a particular team/club can do so by filling out he registration form and submitting it. The applicant will then recieve an email notification, informing them of their entry. The coach of the team/club will then have to accept the applicant or deny the applicant. If only the applicant is accepted, then can login to the website at which point a few more options are available to them.

Coaches login using special username and password for each team/club at which point, more adminitrative controls are available to them. They can accept or deny applicants, grant or deny applicants release from the team/club, as well as input the trophies won for the season into the trophy display. Coaches can only input trophies for their own team and emails are sent to applicant or registered members for any action taken towards them.

Technologies used:

python
flask
sqlite
html and css
gmail
Libraries needed:

os flask flask_session flask_mail tempfile werkzeug.security sqlite3 functools re

Information for Coaches: 

Username - Coach18 Password - Eighteen1

Username - Coachcalor Password - Calor123

Username - Coachdcyo Password - Dcyo1234

Username - Coachunder Password - Underrock1

Username - Coachwhite Password - Whitehouse1

Username - Coachhilltop Password - Hilltop1

Routing:

Each player has a unique username and email address as well as unique id which allows the sessions to remain unique.

Database:

Sqlite is used as the database for this project. It is used to store the table for the application of applicants, registered players, coaches, and trophies for display.

Possible improvements:

More sports clubs can be added. Registered members could be allowed to change data, eg email address and contact.