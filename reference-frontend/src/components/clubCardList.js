import React, { useEffect, useState } from 'react'
import ClubCard from './clubCard'

function ClubCardList() {
    const [clubs, setClubs] = useState([])

    useEffect(() => {
        fetch("/api/clubs")
            .then(res => res.json())
            .then((result) => setClubs(result.clubs))
    }, [])

    return (
        <>
            <section id="clubs">
                {clubs.map((club, index) => {
                    return <ClubCard key={index} club={club} />
                })}
            </section>
        </>
    )
}

export default ClubCardList