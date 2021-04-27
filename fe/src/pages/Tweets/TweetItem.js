import React from "react";
import { View, Image, Text, StyleSheet } from "react-native";

const TweetItem = ({ item: booking }) => {
  return (
    <View style={styles.row}>
      
      {/* <Image style={styles.rowIcon} source={"add an image.webp here"} /> */}
      <View style={styles.rowData}>
      <Text style={styles.rowDataText}>Username :   {booking.user}</Text><br></br>
        {/* <Text style={styles.rowDataText}>First Name :   {booking.firstName}</Text><br></br>
        <Text style={styles.rowDataText}>Last Name :   {booking.lastName}</Text><br></br> */}
        <Text style={styles.rowDataText}>Source :   {booking.source}</Text><br></br>
        <Text style={styles.rowDataText}>Destination :   {booking.destination}</Text><br></br>
        <Text style={styles.rowDataText}>Journey Date :   {booking.journeyDate}</Text><br></br>
      </View>
    </View>
  );
};

const styles = StyleSheet.create({
  row: {
    flexDirection: "row",
    justifyContent: "center",
    alignItems: "center",
    padding: 15,
    marginBottom: 5,
    backgroundColor: "white",
    borderBottomWidth: StyleSheet.hairlineWidth,
    borderBottomColor: "rgba(0,0,0,0.1)"
  },
  rowIcon: {
    width: 64,
    height: 64,
    marginRight: 20,
    borderRadius: "50%",
    boxShadow: "0 1px 2px 0 rgba(0,0,0,0.1)"
  },
  rowData: {
    flex: 1
  },
  rowDataText: {
    fontSize: 17,
    textTransform: "capitalize",
    color: "black"
  },
  rowDataSubText: {
    fontSize: 13,
    opacity: 0.8,
    color: "#a8a689",
    marginTop: 4
  },
  map: {
    width:'10%',
    height:'10%'  
  }
});

export default TweetItem;