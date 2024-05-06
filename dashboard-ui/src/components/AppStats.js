import React, { useEffect, useState } from 'react'
import '../App.css';

export default function AppStats() {
    const [isLoaded, setIsLoaded] = useState(false);
    const [stats, setStats] = useState({});
    const [error, setError] = useState(null)

    const getStats = () => {

        fetch(`http://ec2-44-230-165-6.us-west-2.compute.amazonaws.com/processing/stats`)
            .then(res => res.json())
            .then((result) => {
                console.log("Received Stats")
                setStats(result);
                setIsLoaded(true);
            }, (error) => {
                setError(error)
                setIsLoaded(true);
            })
    }
    useEffect(() => {
        const interval = setInterval(() => getStats(), 2000); // Update every 2 seconds
        return () => clearInterval(interval);
    }, [getStats]);

    if (error) {
        return (<div className={"error"}>Error found when fetching from API</div>)
    } else if (isLoaded === false) {
        return (<div>Loading...</div>)
    } else if (isLoaded === true) {
        return (
            <div>
                <h1>Latest Stats</h1>
                <table className={"StatsTable"}>
                    <tbody>
                        <tr>
                            <th>Borrow Book Records</th>
                            <th>Return Book Records</th>
                        </tr>
                        <tr>
                            <td># Borrowed Books: {stats['num_bb_received']}</td>
                            <td># Returned Books: {stats['num_rb_received']}</td>
                        </tr>
                        <tr>
                            <td colspan="2">Avg of Borrow Book duration: {stats['avg_borrow_duration']}</td>
                        </tr>
                        <tr>
                            <td colspan="2">Avg of Return Book duration: {stats['avg_return_duration']}</td>
                        </tr>
                        <tr>
                            <td colspan="2">Max Return Book late fee: {stats['max_return_late_fee']}</td>
                        </tr>
                    </tbody>
                </table>
                <h3>Last Updated: {stats['last_updated']}</h3>

            </div>
        )
    }
}
