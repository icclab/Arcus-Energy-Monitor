#!/bin/bash
# Copyright 2014 Zuercher Hochschule fuer Angewandte Wissenschaften
# All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.
usage() 
{
cat << help
usage: $0 options

This script run compressions...

OPTIONS:
  -h    Help
  -i    Number of folders to copy the ubuntu-14.04-desktop-amd64.iso (It must be in the same folders as the script)
  -c    Number of compressions

help
}
compressions= 
thread= 

while getopts ":i:c:h" opt; do
  case $opt in
    i)
      thread=$OPTARG
      ;;
    \?)
      echo "Invalid option: -$OPTARG" >&2
      usage
      exit 1
      ;;
     :)
      echo "Option -$OPTARG requires an argument." >&2
      usage
      exit 1
      ;;
    c)
      compressions=$OPTARG
      ;;
    h) usage 
       exit 1
       ;;
  esac
done

mkdir ./temp-$thread
cp ubuntu-14.04-desktop-amd64.iso ./temp-$thread/ >&2
for (( i = 0; i<compressions; ++i )) ;
      do
          gzip ./temp-$thread/ubuntu-14.04-desktop-amd64.iso
          gzip -d ./temp-$thread/ubuntu-14.04-desktop-amd64.iso.gz
      done
