import React, { useEffect, useState } from 'react';
import '../App.css';

export default function EndpointAudit(props) {
    const [isLoaded, setIsLoaded] = useState(false);
    const [log, setLog] = useState(null);
    const [error, setError] = useState(null);
    const [index, setIndex] = useState(null);

    const getAudit = () => {
        const rand_val = Math.floor(Math.random() * 100); // Get a random event from the event store
        fetch(`http://ec2-44-230-165-6.us-west-2.compute.amazonaws.com/audit_log${props.endpoint}?index=${rand_val}`)
            .then(res => res.json())
            .then((result) => {
                console.log("Received Audit Results for " + props.endpoint);
                setLog(result);
                setIndex(rand_val); // Set index here after successful fetch
                setIsLoaded(true);
            }, (error) => {
                setError(error);
                setIsLoaded(true);
            });
    };

    useEffect(() => {
        const interval = setInterval(getAudit, 4000); // Update every 4 seconds
        return () => clearInterval(interval);
    }, [getAudit]);

    if (error) {
        return <div className={"error"}>Error found when fetching from API</div>;
    } else if (!isLoaded) {
        return <div>Loading...</div>;
    } else {
        return (
            <div>
                <h3>{props.endpoint}-{index}</h3>
                {JSON.stringify(log)}
            </div>
        );
    }
}
