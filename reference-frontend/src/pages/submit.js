import React from 'react'
import styled from 'styled-components'

const Centered = styled.div`
    display: block;
    margin-left: auto;
    margin-right: auto;
`

function Submit() {
    return (
        <Centered className="col-md-6 mt-4">
            <form action="/api/clubs" method="post">
                <div className="form-group">
                    <label for="name">Club name</label>
                    <input type="text" className="form-control" id="name" name="name" placeholder="Locust Labs" required></input>
                </div>
                <br></br>
                <div className="form-group">
                    <label for="email">Club description</label>
                    <input type="text" className="form-control" id="description" name="description" placeholder="Club description" required></input>
                </div>
                <button type="submit" className="btn btn-primary">Register club</button>
            </form>
        </Centered>
    )
}

export default Submit