import React, {Component} from 'react';
import InfoBox from './InfoBox';
import {Row, Col, Table, Card} from 'antd';

import gpudb from '../config';

class CitiesInfo extends Component {

  state = {
    allTimeCities: [],
    last24Hours: [],
    mostResponses: [],
    cities: null,
  };

  // Columns of the view table
  columns = [{
    title: 'Url',
    dataIndex: 'url',
    key: 'url',
  }, {
    title: 'Count',
    dataIndex: 'count',
    key: 'count',
  }];

  /**
   * Here we are connecting to the Kinetica JS API and getting information about cities in our events
   * https://www.kinetica.com/docs/api/rest/aggregate_groupby_rest.html#aggregate-groupby-rest
   */
  getAllTimeCitiesData = () => {
    //
    gpudb.aggregate_group_by("event_rsvp", ["city", "COUNT(*)"], 0, 5, {
      "sort_order": "descending",
      "expression": "IS_NULL(city) = 0" // Some of the events doesn't have city allocated, we want to filter those out
    }, (err, response) => {
      if (!err) {

        let cities = [];

        for (let i = 0; i < response.data.column_1.length; i++) {
          cities.push({
            "city": response.data.column_1[i],
            "value": response.data.column_2[i]
          })
        }

        this.setState({allTimeCities: cities})
      }
    });
  };

  /**
   * Here we are connecting to the Kinetica JS API and getting information about cities in our events but we filter it
   * based on the time of the event
   * https://www.kinetica.com/docs/api/rest/aggregate_groupby_rest.html#aggregate-groupby-rest
   */
  getLast24HoursCitiesData = () => {
    gpudb.aggregate_group_by("event_rsvp", ["city", "COUNT(*)"], 0, 5, {
      "sort_order": "descending",
      "expression": "TIMESTAMPDIFF(DAY, rsvp_timestamp, NOW()) < 2 AND IS_NULL(city) = 0"
    }, (err, response) => {
      if (!err) {

        let cities = [];

        for (let i = 0; i < response.data.column_1.length; i++) {
          cities.push({
            "city": response.data.column_1[i],
            "value": response.data.column_2[i]
          })
        }

        this.setState({last24Hours: cities})
      }
    });
  };

  /**
   * Again using aggregate API function to find events url with most responses filtered by specific time
   */
  getMostResponsesUrlData = () => {
    gpudb.aggregate_group_by("event_rsvp", ["url", "COUNT(*)"], 0, 10, {
      "sort_order": "descending",
      "expression": "TIMESTAMPDIFF(DAY, rsvp_timestamp, NOW()) < 2"
    }, (err, response) => {
      if (!err) {
        let data = [];
        for (let i = 0; i < 10; i++) {
          data.push({
            key: i,
            url: (<a href={response.data.column_1[i]}>{response.data.column_1[i]}</a>),
            count: response.data.column_2[i],
          });
        }
        this.setState({mostResponses: data});
      }
    });
  };

  componentWillMount() {
    // Init the loading of the data
    this.getAllTimeCitiesData();
    this.getLast24HoursCitiesData();
    this.getMostResponsesUrlData();
  }

  render() {
    return (
      <div>
        <Row style={{"marginTop": "25px"}}>
          <Col span={8} offset={0}><InfoBox key={"1"}
                                            title={<div style={{textAlign: "center"}}>City with most check-ins<br/>Last
                                              24 hours</div>} context={this.state.last24Hours}/></Col>
          <Col span={8} offset={0}><InfoBox key={"2"}
                                            title={<div style={{textAlign: "center"}}>City with most check-ins<br/>All
                                              time</div>} context={this.state.allTimeCities}/></Col>
          <Col span={8} offset={0}><InfoBox key={"3"}
                                            title={<div style={{textAlign: "center"}}>City with most check-ins<br/>Prediction
                                              for next 24hours</div>} context={this.state.cities}/></Col>
        </Row>
        <Row style={{"margin": "25px"}}>
          <Col span={24} offset={0}>
            <Card title={"Events with the most responses in last 24 hours"} style={{width: "750px", margin: "auto"}}>
              <Table bordered pagination={false} dataSource={this.state.mostResponses} columns={this.columns}/>
            </Card></Col>
        </Row>
      </div>
    )
  }

}

export default CitiesInfo;