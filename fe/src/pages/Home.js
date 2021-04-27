import React from "react";
import PropTypes from "prop-types";
import { withStyles } from "@material-ui/core/styles";

const styles = theme => ({
  root: {
    display: "flex",
    flexWrap: "wrap",
    justifyContent: "space-around",
    overflow: "hidden",
    backgroundColor: theme.palette.background.paper,
    marginTop: '100px',
    opacity: 0.7
  }
});
console.log(window.history);
function Home(props) {
  const { classes } = props;

  return (
      <div className={classes.root}>
        <h1>Uber Bus Booking App</h1>
      </div>
  );
}

Home.propTypes = {
  classes: PropTypes.object.isRequired
};

export default withStyles(styles)(Home);