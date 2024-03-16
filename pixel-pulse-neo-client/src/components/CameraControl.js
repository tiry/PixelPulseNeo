import React, { useEffect, useState } from 'react';

import Camera from 'react-html5-camera-photo';
import 'react-html5-camera-photo/build/css/index.css';


import { useParams } from 'react-router-dom';
import {BASE_URL} from '../services/ApiService'

import ApiService from '../services/ApiService';
import { Container, Grid, TextField, Typography, Button, CardMedia} from '@mui/material';

import TextIncreaseIcon from '@mui/icons-material/TextIncrease';
import TextDecreaseIcon from '@mui/icons-material/TextDecrease';
import SpeedIcon from '@mui/icons-material/Speed';
import TextRotationNoneIcon from '@mui/icons-material/TextRotationNone';
import HeightIcon from '@mui/icons-material/Height';
import TrackChangesIcon from '@mui/icons-material/TrackChanges';
import ExpandIcon from '@mui/icons-material/Expand';

import KeyboardDoubleArrowLeftIcon from '@mui/icons-material/KeyboardDoubleArrowLeft';
import KeyboardDoubleArrowRightIcon from '@mui/icons-material/KeyboardDoubleArrowRight';

const CameraControl = () => {
    
    const handleTakePhoto = (dataUri) => {
      console.log(dataUri)
    }
  
    return (
        <Container maxWidth="lg" >          
          <Typography variant="h4" component="h4"> Control  </Typography>
     

      
          
          <Grid container spacing={2}>
            <Grid item xs={12}>
            <Camera
              onTakePhoto = { (dataUri) => { handleTakePhoto(dataUri); } }
            />
            </Grid>
   
          </Grid>

      </Container>
    );
  };
  
export default CameraControl;
