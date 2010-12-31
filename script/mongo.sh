#!/bin/bash

BASEDIR=/Users/dan/Code/myxiv/mongo
PROGRAM=/usr/local/bin/mongod

start_mongo () 
{
  CMD="$PROGRAM --fork --quiet --dbpath $BASEDIR/$1 --logpath $BASEDIR/$1.log --pidfilepath $BASEDIR/$1.pid"
  mkdir -p $BASEDIR/$1
  case $1 in 
    "master" ) 
      $CMD --master --port 27017
      ;;
    "slave"  ) 
      $CMD --slave --source localhost:27017 --port 27018
      ;;
    * )
      $CMD
      ;;
    esac
}

stop_mongo ()
{
  PIDFILE=$BASEDIR/$1.pid
  if test -f $PIDFILE; then
    kill `cat $PIDFILE`
  else
    echo "No pidfile $PIDFILE found."
    exit 0
  fi
}

if test ! -d $BASEDIR; then
  if mkdir -p $BASEDIR; then
    echo "Created $BASEDIR"
  else
    echo "Error: $BASEDIR invalid"
    exit 0
  fi
fi

if test ! -x $PROGRAM; then
  echo "Error: $PROGRAM not an executable"
  exit 0
fi

case $1 in
  "start" )
    start_mongo "master"
    start_mongo "slave"
    ;;
  "stop" )
    stop_mongo "master"
    stop_mongo "slave"
    ;;
  * )
    echo "mongo.sh start/stop"
    ;;
  esac
