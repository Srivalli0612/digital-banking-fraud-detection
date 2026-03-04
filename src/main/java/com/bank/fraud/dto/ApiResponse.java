package com.bank.fraud.dto;

import java.time.LocalDateTime;

public class ApiResponse<T> {

    private String status;
    private String message;
    private T data;
    private LocalDateTime timestamp;

    public ApiResponse(String status, String message, T data) {
        this.status = status;
        this.message = message;
        this.data = data;
        this.timestamp = LocalDateTime.now();
    }
 
    // Getters
    public String getStatus() { return status; }
    public String getMessage() { return message; }
    public T getData() { return data; }
    public LocalDateTime getTimestamp() { return timestamp; }
}