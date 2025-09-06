# Ticket Inspector Backend

A route optimization system for public transit ticket inspectors that uses mathematical optimization to determine the most efficient inspection routes across transit networks.

## Problem Statement

Public transit systems need to efficiently deploy ticket inspectors to maximize route coverage while minimizing travel time and operational costs. This system solves the challenge of:

- **Route Coverage Maximization**: Visiting as many different transit routes as possible within time constraints
- **Time Optimization**: Minimizing total travel time while ensuring comprehensive coverage
- **Operational Efficiency**: Creating feasible inspection paths that start and end at a designated depot/stop

## How It Works

### Core Algorithm
The system uses **Mixed Integer Linear Programming (MILP)** with the PuLP optimization library to solve a variant of the Traveling Salesman Problem (TSP) with additional constraints:

1. **Objective Function**: Maximize the number of unique transit routes visited
2. **Constraints**:
   - Time window limitations (default: 240 minutes)
   - Flow conservation (each stop has equal in/out edges)
   - Single path requirement (no cycles except returning to start)
   - Route feasibility (only use existing transit connections)

### Technical Approach

#### Data Processing
- **GTFS Data Integration**: Processes General Transit Feed Specification data including:
  - `stops.txt` - Stop locations and metadata
  - `routes.txt` - Transit route definitions
  - `trips.txt` - Trip-to-route mappings
  - `stop_times.txt` - Schedule and timing data

#### Graph Construction
- Builds a 3D adjacency matrix `AdjMatrix[stop_i][stop_j][route_k]`
- Creates time matrix with travel times between consecutive stops
- Handles missing data with reasonable defaults

#### Optimization Variables
- `x[i][j][k]`: Binary variable (1 if inspector travels from stop i to stop j via route k)
- `y[k]`: Binary variable (1 if route k is visited)
- `t[i]`: Continuous variable defining visit order for subtour elimination

## API Endpoints

### GET `/api/:sid`
Generates optimal inspection route starting from the specified stop ID.

**Parameters:**
- `sid` (path parameter): Starting stop ID

**Response:**
```json
{
  "0": {
    "stop_a_id": 123,
    "stop_a_name": "Main Street Station",
    "stop_a_lat": 40.7128,
    "stop_a_lng": -74.0060,
    "stop_a_time": 0,
    "stop_b_id": 124,
    "stop_b_name": "Central Plaza",
    "stop_b_lat": 40.7589,
    "stop_b_lng": -73.9851,
    "stop_b_time": 15,
    "route": 2
  }
}
```

## Local Setup

### Prerequisites
- **Node.js**: Version 10.19.0
- **npm**: Version 6.14.4
- **Python**: Version 3.6+ with pip
- **GTFS Data**: Place your GTFS files in `./data/gtfscecil/`

### Required GTFS Files
```
data/gtfscecil/
├── stops.txt
├── routes.txt  
├── trips.txt
└── stop_times.txt
```

### Installation Steps

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd ticket-Inspector-backend
   ```

2. **Install Node.js dependencies**
   ```bash
   npm install
   ```

3. **Install Python dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Prepare GTFS data**
   - Create the directory structure: `./data/gtfscecil/`
   - Place your GTFS files in this directory
   - Ensure files follow the GTFS specification format

5. **Start the server**
   ```bash
   npm start
   ```

The server will start on port 5000 (or the port specified in `process.env.PORT`).

### Testing the API

```bash
# Example: Get route plan starting from stop ID 1
curl http://localhost:5000/api/1
```

## Configuration

### Time Constraints
Modify the `MaxTime` variable in `get_route_plan.py` to adjust the inspection time window:
```python
MaxTime = 240  # Time in minutes
```

### Transfer Penalties
The system adds time penalties for:
- Route transfers: +5 minutes
- Same-route connections: +2 minutes

## Dependencies

### Backend (Node.js)
- **express**: Web framework for API endpoints
- **python-shell**: Interface for executing Python optimization scripts
- **fs**: File system operations

### Optimization Engine (Python)
- **pandas**: Data manipulation and CSV processing
- **PuLP**: Linear programming optimization
- **pathlib**: File path handling
- **requests**: HTTP requests (if needed for external data)

## Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Client        │────│  Express.js API  │────│ Python Optimizer│
│   Request       │    │   (Node.js)      │    │    (PuLP)       │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                                │                        │
                                │                        │
                         ┌──────▼──────┐         ┌──────▼──────┐
                         │  Route       │         │ GTFS Data   │
                         │  Response    │         │ Processing  │
                         │  (JSON)      │         │ & Graph     │
                         └─────────────┘         │ Building    │
                                                 └─────────────┘
```

## Deployment Notes

### Heroku Deployment
The included `Procfile` supports Heroku deployment:
```
web: pip install -r requirements.txt && npm start
```

### Production Considerations
- Ensure sufficient memory for large GTFS datasets
- Consider caching optimization results for frequently requested routes
- Monitor Python script execution times for performance optimization

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test with sample GTFS data
5. Submit a pull request

## License

ISC License - See package.json for details

## Author

Swati Ahuja
