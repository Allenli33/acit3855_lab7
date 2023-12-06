/* eslint-disable react-hooks/exhaustive-deps */
import React, { useEffect, useState } from 'react';
import '../App.css';

export default function AppHealths() {
    const [isLoaded, setIsLoaded] = useState(false);
    const [healths, setHealths] = useState({});
    const [error, setError] = useState(null);

    const getHealths = () => {
        fetch(`http://messager.eastus2.cloudapp.azure.com/health`)
            .then((res) => res.json())
            .then(
                (result) => {
                    console.log('Received Healths');
                    setHealths(result);
                    setIsLoaded(true);
                },
                (error) => {
                    setError(error);
                    setIsLoaded(true);
                }
            );
    };
    useEffect(() => {
        const interval = setInterval(() => getHealths(), 2000); // Update every 2 seconds
        return () => clearInterval(interval);
    }, [getHealths]);

    if (error) {
        return <div className={'error'}>Error found when fetching from API</div>;
    } else if (isLoaded === false) {
        return <div>Loading...</div>;
    } else if (isLoaded === true) {
        return (
            <div className={'StatsTable'}>
                <h1>Latest Health Status</h1>
                <p>
                    <b>Receiver:</b> {healths['receiver']}
                </p>
                <p>
                    <b>Storage:</b> {healths['storage']}
                </p>
                <p>
                    <b>Processing:</b> {healths['processing']}
                </p>
                <p>
                    <b>Audit:</b> {healths['audit']}
                </p>
                <p>
                    <b>Last Updated:</b> {healths['last_updated']}
                </p>
            </div>
        );
    }
}