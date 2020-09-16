import React from 'react'
import styled from 'styled-components'

const ClubCardContainer = styled.div`
    position: relative;
    display: block;
    width: 420px;
    height: 400px;
    margin: 25px;
    float: left;
    padding: 15px;
    border: 1px solid #DDDDDD;
    border-radius: 15px;
`

const ClubDescription = styled.p`
    padding: 10px;
    display: block;
    height: 55%;
`

function ClubCard(props) {
    return (
        <ClubCardContainer>
            <h4>{props.club.name}</h4>
            <hr></hr>
            <ClubDescription>{props.club.description}</ClubDescription>
        </ClubCardContainer>
    )
}

export default ClubCard