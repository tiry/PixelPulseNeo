import React, { useEffect, useState } from 'react';
import ApiService from '../services/ApiService';
import { Container, Grid, Paper, Typography, Button, Switch } from '@mui/material';
import MemoryIcon from '@mui/icons-material/Memory';
import ThermostatIcon from '@mui/icons-material/Thermostat';
import SpeedIcon from '@mui/icons-material/Speed';
import StorageIcon from '@mui/icons-material/Storage';
import AccessTimeIcon from '@mui/icons-material/AccessTime';
import BatterySaverIcon from '@mui/icons-material/BatterySaver';
import BedtimeIcon from '@mui/icons-material/Bedtime';
import AlarmOnIcon from '@mui/icons-material/AlarmOn';
import NotificationsOffSharpIcon from '@mui/icons-material/NotificationsOffSharp';
import NotificationAddSharpIcon from '@mui/icons-material/NotificationAddSharp';
import {BASE_URL} from '../services/ApiService'

const metricIcons = {
    cpu_freq: <SpeedIcon />,
    python_cpu: <SpeedIcon />,
    cpu_temp: <ThermostatIcon />,
    gpu_temp: <ThermostatIcon />,
    free_mem: <MemoryIcon />,
    used_mem: <MemoryIcon />,
    total_mem: <MemoryIcon />,
    cpu_load1: <SpeedIcon />,
    cpu_load5: <SpeedIcon />,
    cpu_load15: <SpeedIcon />,
    up_time: <AccessTimeIcon />,
    governor : <BatterySaverIcon/>,
  };

const StatusViewer = () => {
    const [metrics, setMetrics] = useState({});
  
    const fetchMetrics = async () => {
      ApiService.getMetrics().then((metrics) => {
        //console.log(metrics)
        setMetrics(metrics)
      })
    };
    useEffect(() => {
      fetchMetrics().catch(console.error);
    }, []);
  
    if (!metrics) {
      return <Typography>Loading...</Typography>;
    }
  
    const handleSleep = () => {
      ApiService.sleep()
      fetchMetrics()
    };

    const handleWakeup = () => {
      ApiService.wakeup()
      fetchMetrics()
    };
    
    const handleToggleWatchDog = (event) => {
      if (event.target.checked)
      {
        ApiService.watchdog("on")
      }
      else
      {
        ApiService.watchdog("off")
      }
      fetchMetrics()
    }
    return (
        <Container maxWidth="lg" >
        <Grid container spacing={3}>
          
          <Grid item xs={12}>
            <Typography variant="h4" component="h4"> Power Management: </Typography>
          </Grid>
          
          <Grid item xs={4}>
          &nbsp; 
            <Button variant="contained" color="primary" startIcon={<BedtimeIcon />} disabled={metrics["sleeping"]==true} fullWidth
                    onClick={() => handleSleep()}>Sleep
            </Button>
            &nbsp; 
            <Button variant="contained" color="primary" startIcon={<AlarmOnIcon />} disabled={metrics["sleeping"]==false} fullWidth
                    onClick={() => handleWakeup()}>Wake&nbsp;Up
            </Button>            
          </Grid>

          <Grid item xs={4}>
            <Typography align="center">{metrics["sleeping"]? "Matrix is asleep" : "Matrix is on"}</Typography>
            <Typography align="center">
            {metrics["sleeping"]? 
            (<img src={`${BASE_URL}/../web/pictures/sleep.png`} width="100%"/>) : 
            (<img src={`${BASE_URL}/../web/pictures/awake.png`} width="100%"/>)}
            </Typography>
          </Grid>  

          <Grid item xs={4}>
          &nbsp; 
            <Typography align="center">{metrics["watchdog_on"]? "Watch dog is running" : "Watch dog disabled"}</Typography>
            &nbsp;
            <Typography align="center">
            {metrics["watchdog_on"] ?
                (<NotificationAddSharpIcon/>
                ) : (<NotificationsOffSharpIcon/>)  
            }
            <Switch
              checked={metrics["watchdog_on"]}
              onChange={handleToggleWatchDog}
           /></Typography>
          </Grid>  
          <Grid item xs={12}>
            <Typography variant="h4" component="h4"> Monitoring: </Typography>
          </Grid>
      
          {Object.entries(metrics).map(([key, value]) => (
            <>
            {['sleeping', 'watchdog_on'].includes(key) ? ( <></>) : ( 
              
            <Grid item xs={12} sm={6} md={3} key={key}>
          
              <Paper elevation={2} sx={{ padding: 2, display: 'flex', alignItems: 'center', gap: 2 }}>
                {metricIcons[key] || <StorageIcon />} {/* Fallback to a default icon if specific one is not found */}
                <div>
                  <Typography variant="h6" component="h2" gutterBottom>
                    {key.replace(/_/g, ' ')}
                  </Typography>
                  <Typography variant="body1">{value}</Typography>
                </div>
              </Paper>
              
            </Grid>
            )}            
            </>
          ))}
        </Grid>
      </Container>
    );
  };
  
export default StatusViewer;
