#!/bin/bash

echo Adding User $1

sudo useradd -m -s /bin/bash -G mausers $1

sudo passwd $1

sudo mkdir /home/$1/mail
sudo chown $1 /home/$1/mail
sudo chgrp $1 /home/$1/mail

sudo mkdir /home/$1/.procmail
sudo chown $1 /home/$1/.procmail
sudo chgrp $1 /home/$1/.procmail

sudo cp .procmailrc /home/$1/.procmailrc
sudo chown $1 /home/$1/.procmailrc
sudo chgrp $1 /home/$1/.procmailrc

sudo touch /home/$1/.fetchmailrc
sudo chown $1 /home/$1/.fetchmailrc
sudo chgrp $1 /home/$1/.fetchmailrc
sudo chmod 600 /home/$1/.fetchmailrc

sudo cp -pr /home/mailact/mail_act /home/$1/



