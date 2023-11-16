import React, { useEffect, useState, useCallback } from 'react';
import '../App.css';

export default function EndpointAudit(props) {
    const [isLoaded, setIsLoaded] = useState(false);
    const [log, setLog] = useState(null);
    const [error, setError] = useState(null);
    const [index, setIndex] = useState(null);

    useEffect(() => {
        // Set index when component mounts
        setIndex(Math.floor(Math.random() * 100));
    }, []);

    const getAudit = useCallback(() => {
        fetch(`http://allenliacit3855.eastus.cloudapp.azure.com:8110${props.endpoint}?index=${index}`)
            .then(res => res.json())
            .then((result) => {
                console.log("Received Audit Results for " + props.endpoint)
                setLog(result);
                setIsLoaded(true);
            }, (error) => {
                setError(error)
                setIsLoaded(true);
            })
    }, [props.endpoint, index]); // Added index to the dependency array

    useEffect(() => {
        const interval = setInterval(getAudit, 4000); // Update every 4 seconds
        return () => clearInterval(interval);
    }, [getAudit]);

    if (error) {
        return (<div className={"error"}>Error found when fetching from API</div>);
    } else if (!isLoaded) {
        return (<div>Loading...</div>);
    } else {
        return (
            <div>
                <h3>{props.endpoint}-{index}</h3>
                {JSON.stringify(log)}
            </div>
        );
    }
}
