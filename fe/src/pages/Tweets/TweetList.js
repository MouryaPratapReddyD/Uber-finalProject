import React from "react";
import { SwipeableFlatList } from "react-native";
//import {SwipeableFlatList} from 'react-native-swipeable-flat-list';
import TweetItem from "./TweetItem";
import TweetActions from "./TweetActions";

const TweetList = ({ bookings }) => {
  return (
    <SwipeableFlatList
      data={bookings}
      bounceFirstRowOnMount={true}
      maxSwipeDistance={160}
      renderItem={TweetItem}
      renderQuickActions={TweetActions}
    />
    
  );
};

export default TweetList;
