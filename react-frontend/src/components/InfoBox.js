import React, {Component} from 'react';

import {Card} from 'antd';

class InfoBox extends Component {

  generateList = () => {
    const context = this.props.context;

    if (!context) {
      return "TBD"
    }

    let listItems = [];
    for (let index in context) {
      if (index === 0) {
        listItems.push(<li key={index}><b>{context[index].city} - {context[index].value}</b></li>)
      } else {
        listItems.push(<li key={index}>{context[index].city} - {context[index].value}</li>)
      }
    }

    return (
      <ul style={{"listStyleType": "circle"}}>
        {listItems}
      </ul>
    );
  };

  render() {
    return (
      <React.Fragment>
        <Card title={this.props.title} style={{width: "250px", margin: "auto"}}>
          {this.generateList()}
        </Card>
      </React.Fragment>

    )
  }

}

export default InfoBox;