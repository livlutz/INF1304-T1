# Use a base image with Java 17
FROM maven:3.8.4-openjdk-17

# Set the working directory
WORKDIR /app

# Copy the pom.xml and download dependencies
COPY pom.xml .
RUN mvn dependency:go-offline

# Copy the rest of the application source code
COPY src ./src

# Build the application
RUN mvn package

# Run the application
CMD ["java", "-jar", "target/consumer-1.0-SNAPSHOT.jar"]
