import axios from 'axios';
import axiosInstance from './axiosInstance';
const apiUrl = process.env.REACT_APP_API_URL;

export const fetchEmails = ({from_date,to_date}) =>{

    const body = {
        from_date,
        to_date
    }
    return axiosInstance.post(`email/fetch_emails_from_gmail`,body );

}


export const cleanEmails = () =>{


    return axiosInstance.get('email/clean_emails');
}
export const fetchCleanEmails = () =>{


    return axiosInstance.get('email/fetch_clean_emails');
}