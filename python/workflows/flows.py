from distributed import Client
from prefect import Flow
import tasks as tasks
import cluster_tasks as ctasks
import job_tasks as jtasks

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
    cluster = ctasks.cluster_init(fcstconf,provider)

    # Setup the job 
    fcstjob = tasks.job_init(cluster, fcstjobfile, 'roms')
 
    # Get forcing data
    forcing = jtasks.get_forcing(fcstjob,sshuser)
 
    # Start the cluster
    cluster_start = ctasks.cluster_start(cluster)
  
    # Run the forecast
    fcst_run = tasks.forecast_run(cluster,fcstjob)
  
    # Terminate the cluster nodes
    cluster_stop = ctasks.cluster_terminate(cluster)
 
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
    postmach = ctasks.cluster_init(postconf,provider)
    pmStarted = ctasks.cluster_start(postmach)
  
    # Push the env, install required libs on post machine
    # TODO: install all of the 3rd party dependencies on AMI
    pushPy = ctasks.push_pyEnv(postmach, upstream_tasks=[pmStarted])
  
    # Start a dask scheduler on the new post machine
    daskclient : Client = ctasks.start_dask(postmach, upstream_tasks=[pmStarted])
  
    # Setup the post job
    plotjob = tasks.job_init(postmach, postjobfile, 'plotting', upstream_tasks=[pmStarted])
  
    # Get list of files from job specified directory
    FILES = jtasks.ncfiles_from_Job(plotjob)
  
    # Make plots
    plots = jtasks.daskmake_plots(daskclient, FILES, plotjob)
    plots.set_upstream([daskclient])
  
    storage_service = tasks.storage_init(provider)
    pngtocloud = tasks.save_to_cloud(plotjob, storage_service, ['*.png'], public=True)
    pngtocloud.set_upstream(plots)
  
    # Make movies
    mpegs = jtasks.daskmake_mpegs(daskclient, plotjob, upstream_tasks=[plots])
    mp4tocloud = tasks.save_to_cloud(plotjob, storage_service, ['*.mp4'], public=True)
    mp4tocloud.set_upstream(mpegs)
  
    closedask = ctasks.dask_client_close(daskclient, upstream_tasks=[mpegs])
    pmTerminated = ctasks.cluster_terminate(postmach,upstream_tasks=[mpegs,closedask])
  
    #######################################################################
  
  return plotflow
 



def test_flow(fcstconf, fcstjobfile ) -> Flow:

  with Flow('fcst workflow') as testflow:

    # Create the cluster object
    cluster = ctasks.cluster_init(fcstconf,provider)

    # Setup the job 
    fcstjob = tasks.job_init(cluster, fcstjobfile, 'roms')

    # Get forcing data
    forcing = jtasks.get_forcing(fcstjob)

    # Start the cluster
    cluster_start = ctasks.cluster_start(cluster)

    # Run the forecast
    fcst_run = tasks.forecast_run(cluster,fcstjob)

    # Terminate the cluster nodes
    cluster_stop = ctasks.cluster_terminate(cluster)

    testflow.add_edge(cluster, fcstjob)
    testflow.add_edge(fcstjob, forcing)
    testflow.add_edge(forcing, cluster_start)
    testflow.add_edge(cluster_start, fcst_run)
    testflow.add_edge(fcst_run, cluster_stop)

    # If the fcst fails, then set the whole flow to fail 
    testflow.set_reference_tasks([fcst_run,cluster_stop])

  return testflow


 
if __name__ == '__main__':

  
  fcstconf = f'../configs/cbofs.config'
  jobfile = f'../jobs/cbofs.00z.fcst'

  fcstflow = test_flow(fcstconf, jobfile)
  fcstflow.run()
 
  
