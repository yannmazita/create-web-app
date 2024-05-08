export interface TokenData {
    access_token: string | null,
    token_type: string | null,
}

export interface UserCreate {
    username: string,
    password: string,
}

export interface User {
    id: string,
    username: string,
    roles: string,
}

export interface ServerStats {
    active_users: number,
}
