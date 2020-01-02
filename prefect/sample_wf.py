#!/usr/bin/env python3

from prefect import Flow, task

@task
def get_ics()
  return

@task
def pre_process()
  return

@task
def configure_model()
  return

@task
def create_cluster()
  return

@task
def run_forecast()
  return

@task
def post_process()
  return

@task
def terminate_cluster()
  return



# Define the floe

with Flow("model run") as flow:
  get_ics()
  configure_model()
  create_cluster('forecast')
  run_forecast()
  terminate_cluster()

  create_cluster('post')
  post_process()


flow.run()

