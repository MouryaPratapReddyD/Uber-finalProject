import React, { useState, useEffect } from 'react';
import { ScrollView, StyleSheet, ActivityIndicator } from "react-native";
import TweetList from "./TweetList";
import axios from 'axios';

require('dotenv').config()

const THome = () => {
  const [bookings, setBookings] = React.useState([]);
  const [loading, setLoading] = React.useState(true);  
  
  useEffect(() => {
    const fetchData = async () => {
      //const res = await fetch("http://localhost:5000/tweets-results");
      //const res = await fetch(`${process.env.REACT_APP_BE_NETWORK}:${process.env.REACT_APP_BE_PORT}/tweets-results`);
      //const res = await fetch(`${process.env.REACT_APP_API_SERVICE_URL}/tweets-results`);
      //const res = await fetch(`http://localhost:5000/bookings-user-week-results?user=${encodeURIComponent(data.user)}`);
      console.log(localStorage.getItem("username"));
      const data = {user: localStorage.getItem("username")};

      if (localStorage.getItem("username") != null) {
        
        console.log("showing bookings");
        
      } else {
        alert("Please login to see bookings!");
      }

      const res = await fetch(`http://localhost:5000/bookings-user-week-results?user=${encodeURIComponent(data.user)}`);
      //const res = await fetch("/bookings-user-week-results?user=${encodeURIComponent(data.user)}");
      
      console.log(res);
      const { results } = await res.json();
      console.log(results);
      setBookings([...results]);
	    setLoading(false);
      console.log(bookings);
    };
 
    //print("Home.js: fetching from " + `${process.env.REACT_APP_API_SERVICE_URL}/tweets-results`)
    fetchData();
  }, []);

  return (
    
    <ScrollView noSpacer={true} noScroll={true} style={styles.container}>
	  {loading ? (
	    <ActivityIndicator
		  style={[styles.centering]}
		  color="#ff8179"
		  size="large"
	    />
	  ) : (
	    <TweetList bookings={bookings} />
	  )}
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: {
    backgroundColor: "#3d3d5c",
    marginTop: '60px',
    opacity:0.75
  },
  centering: {
    alignItems: "center",
    justifyContent: "center",
    padding: 8,
    height: "100vh"
  }
});

export default THome;
