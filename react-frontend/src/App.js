import React, {Component} from 'react';
import './App.css';
import MainMap from './components/MainMap';
import {Row, Col} from 'antd';
import CitiesInfo from "./components/CitiesInfo";


class App extends Component {

  render() {

    return (
      <div className="App">
        <Col span={16} offset={4}>
          <Row>
            <div style={{textAlign: "center"}}>
              <div className="mainTitle">Where we meet?</div>
              <div className="subTitle">Meetup.com API analysis powered by Kinetica platform</div>
            </div>
          </Row>
          <Row>
            <MainMap/>
          </Row>
          <Row>
            <CitiesInfo/>
          </Row>
        </Col>
      </div>
    );
  }
}

export default App;
