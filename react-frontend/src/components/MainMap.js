import React, {Component} from 'react';
import mapboxgl from 'mapbox-gl';
import {gpudb, gpuURL} from "../config";

import {Card, Select, Form, Slider} from 'antd';

// const moment = require('moment');
const kickbox = require('kickbox/dist/kickbox.umd.min.js');

// These are just some of the map style you can use to render your map layer.
const mapStyles = {
    "streets": "mapbox://styles/mapbox/streets-v10",
    "outdoors": "mapbox://styles/mapbox/outdoors-v10",
    "light": "mapbox://styles/mapbox/light-v9",
    "dark": "mapbox://styles/mapbox/dark-v9",
    "satelite": "mapbox://styles/mapbox/satellite-v9"
};

class MainMap extends Component {

    kbConfig = {
        kineticaUrl: gpuURL,
        wmsUrl: gpuURL + '/wms',
        mapboxKey: 'pk.eyJ1IjoibXN2YW5hcHJvZmlxIiwiYSI6ImNqb3R6dDk0YzEzOXgzcHBjcHB4ZGFzc3AifQ.JwAE4uhGh1fr2bz9mvMBmQ',
        tableName: 'event_rsvp',
        xColumnName: 'lon',
        yColumnName: 'lat',
        // geohashColumnName: 'your_geohash_column_name',
        center: [-74.2598555, 40.6971494],
        zoom: 2.0,
        // If using basic authentication
        // username: '',
        // password: ''
    };

    map = null;

    state = {
        currentMapStyle: 'mapbox://styles/mapbox/dark-v9',
        latestDataSeconds: 0,
        latestCity: "...",
        totalData: 0,
        filtering: false,
        filteredViewId: null,
        filteringTimeSpanHours: Infinity,
        map: null,
        layerId: this.kbConfig.tableName + '-raster',
    };

    getLastEventData() {
        gpudb.get_records("event_rsvp", 0, 1, {
            "sort_by": "rsvp_timestamp",
            "sort_order": "descending"
        }, (err, data) => {

            if (!err) {
                const requestedTimeStamp = new Date().getTime();
                const timestamp = data['data'][0]['rsvp_timestamp'];
                const seconds = Math.round((requestedTimeStamp - timestamp) / 1000);
                this.setState({latestDataSeconds: seconds});
                this.setState({latestCity: data['data'][0]['city']});
                this.setState({totalData: data['total_number_of_records']})
            }

        })
    }

    generateMapPicker() {
        let options = [];
        for (let style in mapStyles) {
            options.push(<Select.Option style={{"padding-left": "10px"}} key={style}
                                        value={mapStyles[style]}>{style}</Select.Option>)
        }

        return (
            <Form.Item label="Map style" labelCol={{sm: {span: 9}}} wrapperCol={{sm: {span: 15}}}>
                <Select style={{width: "110px", paddingLeft: 15}} defaultValue="dark"
                        onChange={this.onMapSelectorChange}>
                    {options}
                </Select>
            </Form.Item>

        )

    };

    /************ START OF SECTION HANDLING FILTERING ************/

    /**
     * Filtering of the DATA with Kickbox and Kinetica
     *
     *  The concept of the filtering might look little bit complicated at first but in fact is pretty straightforward.
     *  We will generate new "view" with filtered data inside our Kinetica DB. After that we will just point the kickbox
     *  map layer to that new view. There are few things to think about (name of the view, TTL), you can read more about
     *  in the inline comments.
     *
     *  TLDR:
     *  - Generate new filtered view using gpudb.filter
     *  - Update the kickbox map layer using kickbox.updateWmsLayer
     *
     * */
    updateMapLayerWithFilteredData = () => {

        // First let's call function which will connect to the API and generate new filtered table view
        this.generateFilteredMap().then((view_id) => {

            // Let's save the new filtered view id to the react state, just in case we would need it.
            this.setState({filteredViewId: view_id});

            // const newLayerId = 'layer' + view_id;

            console.log('updating: ', view_id);

            // Update the kinetica table view of our kickbox layer
            kickbox.updateWmsLayer(this.map, {
                wmsUrl: this.kbConfig.wmsUrl,
                layerId: this.state.layerId,
                tableName: view_id
            });

            // this.setState({layerId: newLayerId})
        }).catch((err) => {
            console.error("Failed to generate the filtered map.")
        });
    };
    /**
     * This function connects to Kinetica API and generates new filtered table view inside the DB.
     * @returns {Promise}
     */
    generateFilteredMap = () => {

        // We want to generate unique ID for our view so it doesn't collide, however we should generate the ID's based
        // on some pattern, so if several users request the same filter we don't need to generate new view as we already have it.
        const dateId = new Date().getTime().toString().slice(0, -4); // This generates current timestamp in depth of tens of seconds
        const id = `view_last-${this.state.filteringTimeSpanHours}hours_${dateId}`;

        console.debug("Generating new in Kinetica DB view:", id);

        return new Promise((resolve, reject) => {
            // Note the collection name and TTL. It's important to put a view into the collection so it's not polluting our DB
            // The TTL parameter sets the max time to live of our view. Because we assume our filters are unique we don't want to
            // store them for a long time.
            gpudb.filter('event_rsvp', id,
                (this.state.filteringTimeSpanHours !== Infinity ?
                    `TIMESTAMPDIFF(HOUR, rsvp_timestamp, NOW()) < ${this.state.filteringTimeSpanHours} AND ` :
                    '') + 'IS_NULL(city) = 0'
                , {
                    "collection_name": 'filtered_views_by_time',
                    "ttl": "2" // This is in minutes
                }, (err) => {
                    if (!err) {
                        console.debug(`Success - New view in Kinetica DB with id ${id} created`);
                        resolve(id);
                    } else {

                        if (err.message.match('^ Result set: view_last-\\S+hours_\\d+ already exists \\(TM\\/SMh:2297\\); code:1 \'Error\'$')) {
                            console.debug('View already exists, not loading new view')
                            resolve(id)
                        } else {
                            console.error(`New view in Kinetica DB with id ${id} failed to created, ${err}`);
                            reject(err);
                        }
                    }
                })
        });
    };

    /************ END OF SECTION HANDLING FILTERING ************/

    generateMap = () => {

        console.log("Generating the MAP");

        this.getLastEventData();

        const me = this;

        kickbox.initMap({
            mapDiv: 'map',
            mapboxgl: mapboxgl,
            mapboxKey: this.kbConfig.mapboxKey,
            kineticaUrl: this.kbConfig.kineticaUrl,
            wmsUrl: this.kbConfig.wmsUrl,
            zoom: this.kbConfig.zoom,
            center: this.kbConfig.center,
            mapStyle: this.state.currentMapStyle,
        }).then(function (map) {

            me.map = map;

            // Add a raster layer to the map
            kickbox.addWmsLayer(map, {
                layerType: 'heatmap',
                layerId: me.state.layerId,
                wmsUrl: me.kbConfig.wmsUrl,
                tableName: me.kbConfig.tableName,
                xAttr: me.kbConfig.xColumnName,
                yAttr: me.kbConfig.yColumnName,
                // or if using WKT
                // geoAttr: this.kbConfig.wktColumnName,
                renderingOptions: {
                    POINTCOLORS: 'FF0000',
                    LABEL_TEXT_STRING: 'name',
                    POINTSIZES: 10
                },
            });

        });
    };

    // This is initial map render
    componentDidMount() {
        this.generateMap();
    }

    onFilteringTimespanChange = (selected) => {
        let value;
        switch (selected) {
            case 0:
                value = Infinity;
                break;
            case 1:
                value = 1;
                break;
            case 2:
                value = 4;
                break;
            case 3:
                value = 12;
                break;
            case 4:
                value = 24;
                break;
            case 5:
                value = 48;
                break;
            default:
                value = 0;
                break;
        }
        this.setState({filteringTimeSpanHours: value}, this.updateMapLayerWithFilteredData)
    };

    onMapSelectorChange = (value) => {
        this.setState({...this.state, currentMapStyle: value}, () => {
            // Generate the new map AFTER the new state is applied
            this.generateMap();
        });

    };

    render() {
        return (
            <div>
                {/*<Col span={20}>*/}
                <div style={{boxSizing: 'border-box', width: "100%", height: "500px", position: "relative"}}>
                    <div id='map' style={{width: "100%", height: "100%"}}/>
                    <Card title="Meetups locations" style={{width: "250px", position: "absolute", top: 25, left: 25}}>
                        This map displays locations of planned meetups.
                        <br/><br/>
                        {this.generateMapPicker()}
                        {this.state.filteringTimeSpanHours !== Infinity ? `See events from last ${this.state.filteringTimeSpanHours} hours.` :
                            'See all events.'
                        }
                        <Slider defaultValue={0} min={0} tooltipVisible={false} max={5}
                                marks={{0: "all", 1: "1", 2: "4", 3: "12", 4: "24", 5: "48"}}
                                onChange={this.onFilteringTimespanChange}/>
                    </Card>
                </div>
                <div style={{textAlign: "center"}}>
                    The points on the map are generated on the fly by Kinetica. The latest Meetup data
                    are <b>{this.state.latestDataSeconds}s</b> old
                    from event in <b>{this.state.latestCity ? this.state.latestCity : "without specified location."}</b>.
                </div>
            </div>

        )
    }

}

export default MainMap;
