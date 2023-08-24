import { Container } from "@mui/system";
import React, { useEffect, useState } from "react";
import { DataGrid } from "@mui/x-data-grid";
import styles from "./Dashboard.module.css";
import { DatePicker } from "@mui/x-date-pickers";
import { Button, Grid, InputLabel } from "@mui/material";
import Paper from "@mui/material/Paper";
import { styled } from "@mui/material/styles";
import dayjs from "dayjs";
import {
  cleanEmails,
  fetchCleanEmails,
  fetchEmails,
} from "../../api/dashboard";

// const columns = [
//   { field: "id", headerName: "ID", width: 70 },
//   { field: "firstName", headerName: "First name", width: 130 },
//   { field: "lastName", headerName: "Last name", width: 130 },
//   {
//     field: "age",
//     headerName: "Age",
//     type: "number",
//     width: 90,
//   },
//   {
//     field: "fullName",
//     headerName: "Full name",
//     description: "This column has a value getter and is not sortable.",
//     sortable: false,
//     width: 160,
//     valueGetter: (params) =>
//       `${params.row.firstName || ""} ${params.row.lastName || ""}`,
//   },
// ];
const columns = [
  { field: "from", headerName: "From", width: 200 },

//   { field: "received_date", headerName: "Received Date", width: 50 },
  { field: "text", headerName: "Text", width: 500 },
  { field: "label", headerName: "Label", width: 100 },
  // ... other columns
];

// const rows = [
//   { id: 1, lastName: "Snow", firstName: "Jon", age: 35 },
//   { id: 2, lastName: "Lannister", firstName: "Cersei", age: 42 },
//   { id: 3, lastName: "Lannister", firstName: "Jaime", age: 45 },
//   { id: 4, lastName: "Stark", firstName: "Arya", age: 16 },
//   { id: 5, lastName: "Targaryen", firstName: "Daenerys", age: null },
//   { id: 6, lastName: "Melisandre", firstName: null, age: 150 },
//   { id: 7, lastName: "Clifford", firstName: "Ferrara", age: 44 },
//   { id: 8, lastName: "Frances", firstName: "Rossini", age: 36 },
//   { id: 9, lastName: "Roxie", firstName: "Harvey", age: 65 },
// ];

const Item = styled(Paper)(({ theme }) => ({
  backgroundColor: theme.palette.mode === "dark" ? "#1A2027" : "#fff",
  ...theme.typography.body2,
  padding: theme.spacing(1),
  textAlign: "center",
  color: theme.palette.text.secondary,
}));

const Dashboard = () => {
  const today = dayjs();
  const yesterday = dayjs().subtract(1, "day");

  const [fromDate, setFromDate] = useState(yesterday);
  const [toDate, setToDate] = useState(today);
  const [rows, setRows] = useState([]);

  const handleFetchEmails = () => {
    const currentFromDate = dayjs(fromDate).toJSON();
    const currentToDate = dayjs(toDate).toJSON();

    console.log(currentFromDate, currentToDate);

    fetchEmails({ from_date: currentFromDate, to_date: currentToDate })
      .then((res) => {
        console.log(res);
      })
      .catch((err) => {
        console.log(err);
      });
  };

  const handleCleanEmails = () => {
    cleanEmails()
      .then((res) => {
        console.log(res.data);
      })
      .catch((err) => {
        console.log(err);
      });
  };

  const handleFetchCleanEmails = () => {
    fetchCleanEmails()
      .then((res) => {
        const email_arr = res.data.emails;
        console.log(email_arr);
        setRows(
          email_arr.map((item) => ({
            id: item._id,
            from: item.from,
            label: item.label,
            received_date: item.received_date,
            text: item.text,
            // ... other fields
          }))
        );
      })
      .catch((err) => {
        console.log(err);
      });
  };

  return (
    <Container sx={{ paddingTop: "40px", paddingBottom: "40px" }}>
      <Grid container spacing={2}>
        <Grid item xs={6} md={6}>
          <Item>
            <InputLabel htmlFor="from-date">From Date</InputLabel>
            <DatePicker
              id="from-date"
              value={fromDate}
              onChange={(newValue) => setFromDate(newValue)}
              disableFuture
            />
          </Item>
        </Grid>
        <Grid item xs={6} md={6}>
          <Item>
            <InputLabel htmlFor="to-date">To Date</InputLabel>
            <DatePicker
              id="to-date"
              value={toDate}
              disableFuture
              onChange={(newValue) => setToDate(newValue)}
            />
          </Item>
        </Grid>
        <Grid item xs={6} md={4} className={styles.buttonContainer}>
          <Button variant="outlined" onClick={handleFetchEmails}>
            Retrive Gmail Emails
          </Button>
        </Grid>
        <Grid item xs={6} md={4} className={styles.buttonContainer}>
          <Button variant="outlined" onClick={handleCleanEmails}>
            Clean Emails
          </Button>
        </Grid>
        <Grid item xs={6} md={4} className={styles.buttonContainer}>
          <Button variant="outlined" onClick={handleFetchCleanEmails}>
            Fetch Clean Emails
          </Button>
        </Grid>
        <Grid item xs={6} md={12}>
          <Item>
            <DataGrid
              rows={rows}
              columns={columns}
              initialState={{
                pagination: {
                  paginationModel: { page: 0, pageSize: 10 },
                },
              }}
              pageSizeOptions={[5, 10]}
              checkboxSelection
            />
          </Item>
        </Grid>
      </Grid>
    </Container>
  );
};

export default Dashboard;
