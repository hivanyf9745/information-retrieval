import { createSlice } from "@reduxjs/toolkit";

const initialState = {
  results: {},
};

export const resultSlice = createSlice({
  name: "searchResults",
  initialState,
  reducers: {
    fetchResults: (state, action) => {
      state.results = action.payload;
    },
  },
});

// Action creators are generated for each case reducer function
export const { fetchResults } = resultSlice.actions;

export default resultSlice.reducer;
