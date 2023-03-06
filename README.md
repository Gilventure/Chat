![Chat Banner](https://user-images.githubusercontent.com/127144941/223240135-27031ec5-2b8f-49c3-b34f-35df806021dc.jpg)
# A simple P2P chat desktop application, built in Python
Chat was inspired from the simple times of AOL Instant Messensger and MSN Messenger. A time when dial-up was king, and the sound of a connecting modem was the sound of pure anticipation, hope that you would successfully connect to the interent before someone in the house tried making a phone call, and hope that your friends were all there once you finally got "online".

This is a personal project, mostly just for fun, and to help build a deeper understanding of python, sockets & networking.

The idea is that anyone in a home, office, or over the web, can fire up a Chat server and share their IP with others that would like to join them for a digital chat. Anyone that would like to contribute to the project is welcome, new ideas are welcome, you may use this code as your own to start your own app, or you can download the .exe and just run the app for you and your friends.

# Screenshots

![Login](https://user-images.githubusercontent.com/127144941/223234964-b884d08e-5180-4fe5-ac86-d1ca3385e0b2.PNG)
![Chat](https://user-images.githubusercontent.com/127144941/223234960-02c85d90-3920-4e3e-8c07-e2d6b437230f.PNG)

![Help](https://user-images.githubusercontent.com/127144941/223234962-acdf1f81-07d8-4d4b-843f-6f531f6f48a8.PNG)
![Settings](https://user-images.githubusercontent.com/127144941/223234966-057aaa3d-d392-4df2-bf3f-95ec76d6c979.PNG)

# Python & Modules

Chat uses:
* Python 3.9.6 (https://www.python.org/downloads/)
* CustomTkinter 5.1.2 (install with: pip install customtkinter) docs on github.com
* Custom-Tooltip 1.3 (install with: pip install Custom-Tooltip) docs on pypi.org
* Various other built in Python modules (see Chat.py)

# Dependencies & Files

* User settings for Chat are saved in settings.txt using the JSON module
* Various files for icons and notification sounds are provided in main
* Pyinstaller has been used to package a distribution "Chat" folder containing an EXE that will run the current version of Chat
