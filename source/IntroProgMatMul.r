A <- matrix(c(1, 3, 2, 4), nrow=2, ncol=2, byrow = TRUE)
B <- matrix(c(5, 7, 6, 8), nrow=2, ncol=2, byrow = TRUE)

print("The product AB is:")
print(A %*% B)
