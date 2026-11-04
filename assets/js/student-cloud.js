(function(){
'use strict';
const url=window.TA_SUPABASE_URL,key=window.TA_SUPABASE_ANON_KEY;
if(!url||!key||!window.supabase){window.TAStudentCloud={ready:false};return}
const client=window.supabase.createClient(url,key,{auth:{persistSession:true,autoRefreshToken:true,detectSessionInUrl:true}});
async function user(){const {data,error}=await client.auth.getUser();return error?null:data.user}
async function profile(){const u=await user();if(!u)return null;const {data,error}=await client.from('student_profiles').select('first_name,last_name').eq('user_id',u.id).maybeSingle();if(error)throw error;if(!data && u.user_metadata?.first_name && u.user_metadata?.last_name){await saveProfile(u.user_metadata.first_name,u.user_metadata.last_name);return {first_name:u.user_metadata.first_name,last_name:u.user_metadata.last_name}}return data}
async function saveProfile(first,last){const u=await user();if(!u)throw Error('Giriş yapınız');const {error}=await client.from('student_profiles').upsert({user_id:u.id,first_name:first.trim(),last_name:last.trim()},{onConflict:'user_id'});if(error)throw error}
async function save(progressKey,payload){const u=await user();if(!u)return false;if(!/^ta-[\w-]{1,170}$/.test(progressKey))throw Error('Geçersiz anahtar');const {error}=await client.from('student_progress').upsert({user_id:u.id,progress_key:progressKey,payload,updated_at:new Date().toISOString()},{onConflict:'user_id,progress_key'});if(error)throw error;return true}
async function load(progressKey){const u=await user();if(!u)return null;const {data,error}=await client.from('student_progress').select('payload').eq('user_id',u.id).eq('progress_key',progressKey).maybeSingle();if(error)throw error;return data?data.payload:null}
window.TAStudentCloud={ready:true,client,user,profile,saveProfile,save,load};
})();