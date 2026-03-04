package com.bank.fraud.dto;

import java.math.BigDecimal;
import java.time.LocalDateTime;

import com.fasterxml.jackson.annotation.JsonFormat;

import jakarta.persistence.PrePersist;
import jakarta.validation.constraints.*;

public class TransactionRequestDTO {
 
    @NotBlank(message = "Transaction ID is required")
    private String transactionId;

    @NotBlank(message = "Sender Account Number is required")
    @Pattern(regexp = "ACC\\d+", message = "Account number must start with ACC")
    private String senderAccountNumber;

    @NotBlank(message = "Receiver Account Number is required")
    @Pattern(regexp = "ACC\\d+", message = "Account number must start with ACC")
    private String receiverAccountNumber;

	@NotNull(message = "Amount is required")
    @Positive(message = "Amount must be greater than 0")
    private BigDecimal amount;

	@NotBlank(message = "Transaction Type is required")
    private String transactionType;

    @NotBlank(message = "Location is required")
    private String location;

    @NotBlank(message = "Device ID is required")
    private String deviceId;

    @NotBlank(message = "Merchant is required")
    private String merchant;

    @NotBlank(message = "Sender name is required")
    private String senderName;
    
    @NotBlank(message = "Receiver name is required")
    private String receiverName;
    
 
    @NotBlank(message = "IP Address is required")
    private String ipAddress;

    @NotBlank(message = "Status is required")
    private String status;
    
//    @NotNull(message = "Transaction time is required")
//    @JsonFormat(pattern = "yyyy-MM-dd'T'HH:mm:ss")
//    private LocalDateTime transactionTime;
        
    
    // Getters & Setters

	public String getTransactionId() {
		return transactionId;
	}

	public void setTransactionId(String transactionId) {
		this.transactionId = transactionId;
	}

	public String getSenderName() {
		return senderName;
	}

	public void setSenderName(String senderName) {
		this.senderName = senderName;
	}

	public String getReceiverName() {
		return receiverName;
	}

	public void setReceiverName(String receiverName) {
		this.receiverName = receiverName;
	}
	
	
	public BigDecimal getAmount() {
		return amount;
	}

	public void setAmount(BigDecimal amount) {
		this.amount = amount;
	}

	public String getTransactionType() {
		return transactionType;
	}

	public void setTransactionType(String transactionType) {
		this.transactionType = transactionType;
	}

	public String getLocation() {
		return location;
	}

	public void setLocation(String location) {
		this.location = location;
	}

	public String getDeviceId() {
		return deviceId;
	}

	public void setDeviceId(String deviceId) {
		this.deviceId = deviceId;
	}

	public String getMerchant() {
		return merchant;
	}

	public void setMerchant(String merchant) {
		this.merchant = merchant;
	}

	public String getSenderAccountNumber() {
		return senderAccountNumber;
	}

	public void setSenderAccountNumber(String senderAccountNumber) {
		this.senderAccountNumber = senderAccountNumber;
	}

	public String getReceiverAccountNumber() {
		return receiverAccountNumber;
	}

	public void setReceiverAccountNumber(String receiverAccountNumber) {
		this.receiverAccountNumber = receiverAccountNumber;
	}

	public String getIpAddress() {
		return ipAddress;
	}

	public void setIpAddress(String ipAddress) {
		this.ipAddress = ipAddress;
	}

	public String getStatus() {
		return status;
	}

	public void setStatus(String status) {
		this.status = status;
	}
    
//	public LocalDateTime getTransactionTime() {
//		return transactionTime;
//	}
//
//	public void setTransactionTime(LocalDateTime transactionTime) {
//		this.transactionTime = transactionTime;
//	}
    
}