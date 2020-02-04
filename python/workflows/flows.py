from prefect import Flow
import workflow_tasks as tasks

provider = 'AWS'

def fcst_flow(fcstconf, fcstjobfile, sshuser) -> Flow:

  #fcstconf = f'{curdir}/configs/liveocean.config'
  #print(f"DEBUG: fcstconf is {fcstconf}")
  #fcstjobfile = 'garbage'

  with Flow('fcst workflow') as fcstflow:

    #####################################################################
    # FORECAST
    #####################################################################

    # Create the cluster object
    cluster = tasks.cluster_init(fcstconf,provider)

    # Setup the job 
    fcstjob = tasks.job_init(cluster, fcstjobfile, 'roms')
 
    # Get forcing data
    forcing = tasks.get_forcing(fcstjob,sshuser)
 
    # Start the cluster
    cluster_start = tasks.cluster_start(cluster)
  
    # Run the forecast
    fcst_run = tasks.forecast_run(cluster,fcstjob)
  
    # Terminate the cluster nodes
    cluster_stop = tasks.cluster_terminate(cluster)
 
    fcstflow.add_edge(cluster, fcstjob)
    fcstflow.add_edge(fcstjob, forcing)
    fcstflow.add_edge(forcing, cluster_start)
    fcstflow.add_edge(cluster_start, fcst_run)
    fcstflow.add_edge(fcst_run, cluster_stop)

    # If the fcst fails, then set the whole flow to fail 
    fcstflow.set_reference_tasks([fcst_run,cluster_stop])

  return fcstflow




def plot_flow(postconf, postjobfile) -> Flow:

  with Flow('plotting') as plotflow:
  
    #####################################################################
    # POST Processing
    #####################################################################
  
    # Start a machine
    postmach = tasks.cluster_init(postconf,provider)
    pmStarted = tasks.cluster_start(postmach)
  
    # Push the env, install required libs on post machine
    # TODO: install all of the 3rd party dependencies on AMI
    pushPy = tasks.push_pyEnv(postmach, upstream_tasks=[pmStarted])
  
    # Start a dask scheduler on the new post machine
    daskclient : Client = tasks.start_dask(postmach, upstream_tasks=[pmStarted])
  
    # Setup the post job
    plotjob = tasks.job_init(postmach, postjobfile, 'plotting', upstream_tasks=[pmStarted])
  
    # Get list of files from job specified directory
    FILES = tasks.ncfiles_from_Job(plotjob,"ocean_his_*.nc")
  
    # Make plots
    plots = tasks.daskmake_plots(daskclient, FILES, plotjob)
    plots.set_upstream([daskclient])
  
    storage_service = tasks.storage_init(provider)
    pngtocloud = tasks.save_to_cloud(plotjob, storage_service, ['*.png'], public=True)
    pngtocloud.set_upstream(plots)
  
    # Make movies
    mpegs = tasks.daskmake_mpegs(daskclient, plotjob, upstream_tasks=[plots])
    mp4tocloud = tasks.save_to_cloud(plotjob, storage_service, ['*.mp4'], public=True)
    mp4tocloud.set_upstream(mpegs)
  
    closedask = tasks.dask_client_close(daskclient, upstream_tasks=[mpegs])
    pmTerminated = tasks.cluster_terminate(postmach,upstream_tasks=[mpegs,closedask])
  
    #######################################################################
  
  return plotflow
 
 
if __name__ == '__main__':
  pass
