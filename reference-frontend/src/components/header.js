import React, { useEffect, useState } from 'react'
import styled from 'styled-components'

const ClubsIntro = styled.div`
    padding-top: 30px;
    padding-bottom: 30px;

    color: #FFFFFF;
    background-color: #469CE7;
`

const ClubCount = styled.span`
    font-size: 22px;
    font-weight: bold;
    color: #49DDEE;
`

const TitleSpan = styled.span`
    color: #CCCCCC;
`

const Centered = styled.div`
    display: block;
    margin-left: auto;
    margin-right: auto;
`

function Header() {
    const [clubs, setClubs] = useState([])

    useEffect(() => {
        fetch("/api/clubs")
            .then(res => res.json())
            .then((result) => setClubs(result.clubs))
    }, [])

    return (
        <>
            <ClubsIntro className="row">
                <Centered className="col-md-8 text-center">
                    <h1>Welcome to <TitleSpan>Locust Labs</TitleSpan>!</h1>
                    <h6>Here you can learn and review all of the <ClubCount>{Object.keys(clubs).length}</ClubCount> student clubs on campus!</h6>
                </Centered>
            </ClubsIntro>
        </>
    )
}

export default Header