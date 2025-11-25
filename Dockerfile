# Dockerfile for ASP.NET Core Web App
FROM mcr.microsoft.com/dotnet/aspnet:8.0 AS base
WORKDIR /app
EXPOSE 80
EXPOSE 443

FROM mcr.microsoft.com/dotnet/sdk:8.0 AS build
WORKDIR /src
COPY ["DACN/DACN.sln", "./"]
COPY ["DACN/AdminWeb.csproj", "DACN/"]
COPY ["DACN/Controllers", "DACN/Controllers"]
COPY ["DACN/Models", "DACN/Models"]
COPY ["DACN/Views", "DACN/Views"]
COPY ["DACN/wwwroot", "DACN/wwwroot"]
COPY ["DACN/Program.cs", "DACN/"]
RUN dotnet restore "DACN/AdminWeb.csproj"
RUN dotnet build "DACN/AdminWeb.csproj" -c Release -o /app/build

FROM build AS publish
RUN dotnet publish "DACN/AdminWeb.csproj" -c Release -o /app/publish

FROM base AS final
WORKDIR /app
COPY --from=publish /app/publish .
ENTRYPOINT ["dotnet", "AdminWeb.dll"]
