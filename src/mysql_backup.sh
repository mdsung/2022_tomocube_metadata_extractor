#!/bin/bash

mysqldump --column-statistics=0 -u admin -p -P 13306 -h 103.22.220.149 tomocube > tomocube_label.sql