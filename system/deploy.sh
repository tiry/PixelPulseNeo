#!/bin/bash

sudo cp system/*.service /lib/systemd/system/.

systemctl daemon-reload

