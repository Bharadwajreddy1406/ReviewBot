import axios from 'axios';

export const LoginUser = async (userData) => {
  const { email, password } = userData;
  console.log("email:", email, "password:", password);
  const response = await axios.post(`/login`, { email, password });
  console.log(response.status);
  if (response.status !== 200) {
    throw new Error(response.data);
  }
  return response.data;
};

export const SignUpUser = async (userData) => {
  try {
    const { username, email, password } = userData;
    console.log("name:", username, "email:", email, "password:", password);
    const response = await axios.post(`/signup`, { username, email, password });
    console.log(response.status);
    if (response.status !== 201) {
      
      throw new Error(response.data);
    }
    console.log(response.data);
    return response.data;
  } catch (error) {
    console.error("Error signing up:", error);
    throw error;
  }
};

export const checkAuthStatus = async () => {
  console.log("entered auth status");
  try {
    const res = await axios.get(`/authstatus`);
    console.log(res.data);
    return res.data;
  } catch (error) {
    console.error("Error checking auth status:", error);
    throw error;
  }
};

export const LogoutUser = async () => {
  try {
    await axios.get(`/logout`);
  } catch (error) {
    console.error('Error logging out:', error);
  }
};

export const getChatResponse = async (text) => {
  try {
    const response = await axios.post(`/chat_response`, { text });
    if (response.status !== 200) {
      throw new Error(response.data);
    }
    return response.data;
  } catch (error) {
    console.error('Error fetching AI response:', error);
    throw error;
  }
};